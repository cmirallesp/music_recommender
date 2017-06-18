
import Debug exposing (log)
import Json.Decode exposing (field, int, string, list, Decoder)
import Json.Encode exposing (encode, object,string, int, Value)

import Html exposing (text, div, input, button, p, select,label,h1,h2,h3,h4,h5,h6,fieldset, Html)
import Html.Attributes exposing (value,multiple,style,placeholder,class)
import Html.Events exposing (onClick, onInput)
import Html exposing (program)
import Http exposing (get, post, request, jsonBody, Error, Response, Error(..), Body)
import Task  exposing (Task, succeed, fail, andThen, mapError)   

import Bootstrap.CDN as CDN
import Bootstrap.Form as Form
import Bootstrap.Form.Input as Input
import Bootstrap.Grid as Grid
import Bootstrap.Grid.Col as Col
import Bootstrap.Grid.Row as Row 
import Bootstrap.Button as Button
import Bootstrap.Card as Card
import Bootstrap.Card exposing (header, block, custom, config)
main =
  Html.program
    { init = init 
    , view = view
    , update = update
    , subscriptions = subscriptions
    }

subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none


-- MODEL
type alias ArtistRecommendation=
  { full_name: String
  , score: String
  }


type alias User =
  { user_id: String
  , artists: List (Artist)
  }
  
type alias Artist =
  { id : String
  , full_name : String
  }

type alias Model =
  { user_id: String
  , user_name: String
  , artists : List Artist
  , selected: List Artist
  , recommendation: List ArtistRecommendation
  , created: Bool
  }

model : Model
model =
  { user_id=""
  , user_name =""
  , artists=[] 
  , selected=[]
  , recommendation=[]
  , created = False
  }

init : (Model, Cmd Msg)
init =
  ( model, Cmd.none )

artistRecommendationDecoder: Decoder ArtistRecommendation
artistRecommendationDecoder = 
  Json.Decode.map2 ArtistRecommendation
    (field "full_name" Json.Decode.string)
    (field "score" Json.Decode.string)

recommendationDecorder : Decoder (List ArtistRecommendation)
recommendationDecorder =
  Json.Decode.list artistRecommendationDecoder

userDecoder : Decoder User
userDecoder =
    Json.Decode.map2 User
      (field "user_id" Json.Decode.string)
      (field "artists" listArtistsDecoder)

listArtistsDecoder: Decoder (List Artist)
listArtistsDecoder=
  Json.Decode.list artistDecoder

artistDecoder : Decoder Artist
artistDecoder =
    Json.Decode.map2 Artist
        (field "id"   Json.Decode.string)
        (field "full_name"  Json.Decode.string)

-- update

type Msg
  = CreateUser
  | ChgName String
  | AddArtist (Artist)
  | UserCreated (Result Http.Error (User))
  | Cancel
  | SaveArtistsOfUser
  | SaveArtist (Result Http.Error (List ArtistRecommendation))


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    CreateUser ->
      (model, saveUser model.user_name )
    
    ChgName name ->
      ({model| user_name = name}, Cmd.none)

    AddArtist artist ->
      if (List.member artist model.selected) then
        (model, Cmd.none)
      else
        ({model | selected=artist::model.selected} , Cmd.none)  
        
    UserCreated (Ok new_user) ->
      ( { model | user_id= new_user.user_id, artists=new_user.artists, created = True }, Cmd.none)

    UserCreated (Err _) ->
      ( model, Cmd.none)

    Cancel ->
      ({ model | artists=[], selected = [], recommendation=[],created = False }, Cmd.none)

    SaveArtist (Ok res) ->
      ({model | recommendation=res, created = False}, Cmd.none)


    SaveArtist (Err _) ->
      (model, Cmd.none)

    SaveArtistsOfUser ->
      if model.created then
        (model, saveArtistsOfUser model)            
      else
        (model, Cmd.none)
     -- Boilerplate: Mdl action handler.


encodeSelectedArtists: List Artist -> Value
encodeSelectedArtists selectionList =
  object    
      ( List.map (\{id} -> ( id,Json.Encode.int 1)) selectionList)
    


saveArtistsOfUser : Model -> Cmd Msg
saveArtistsOfUser model = 
  let 
    json = Http.jsonBody <| 
      object
        [ ( "selected", (encodeSelectedArtists model.selected)),
          ( "user_id", (Json.Encode.string model.user_id))
        ]
  in 
    sendPost SaveArtist ("http://localhost:8887/user_artists") recommendationDecorder json

saveUser : String -> Cmd Msg
saveUser name=
  let
    json =Http.jsonBody <|
      object
      [ ("user_name", (Json.Encode.string name))]
  in      
    sendPost UserCreated ("http://localhost:8887/user") userDecoder json

sendGet : (Result Error a -> msg) -> String -> Decoder a -> Cmd msg
sendGet msg url decoder =
  Http.get url decoder |> Http.send msg

sendPost : (Result Error a -> msg) -> String -> Decoder a -> Body -> Cmd msg
sendPost msg url decoder body2 =
    Http.post url body2 decoder |> Http.send msg
    
-- VIEW

showSelection : Model -> Bool
showSelection model = model.created || model.recommendation /= []

viewAllArtists: Model -> List (Html Msg)
viewAllArtists model=
  let 
    title = if (showSelection model) then "Artists" else ""
  in
    if (showSelection model) then
      [ Card.config []
          |> Card.header [ class "text-center" ]  
              [ h3 [ class "mt-2" ] [text title] ]
          |> Card.block []
            [ Card.custom <|
                Grid.container [class "pre-scrollable",style [("text-align","center")]]
                  (List.map (\artist -> 
                      Grid.row []
                        [ Grid.col [] 
                            [ label [] [ text artist.full_name ]]
                        , Grid.col []
                            [ Button.button 
                              [ Button.roleLink
                              , Button.onClick (AddArtist artist)
                              ] [text "Add"]
                            ]
                        ]
                  ) model.artists)
            ]
          |> Card.view 
      ]
    else
      [text ""]
    

viewSelected: Model -> List (Html Msg) 
viewSelected model=
  let 
    title = if  (showSelection model) then "Selection" else ""
  in
    if (showSelection model) then
      [ Card.config []
          |> Card.header [ class "text-center" ]  
              [ h3 [ class "mt-2" ] [text title] ]
          |> Card.block []
            [ Card.custom <|
                Grid.container [class "pre-scrollable", style [("text-align","center")]]
                  ( List.map (\artist ->
                      Grid.row []
                        [ Grid.col []
                          [ label [] [text artist.full_name]]
                        ]
                  ) model.selected)
            ]
          |> Card.view 
      ]
    else
      [text ""]
    

viewRecommendation: Model -> List (Html Msg) 
viewRecommendation model=
  let 
    title = if (showSelection model) then "Recommendation" else ""
  in
    if (showSelection model) then
      [ 
        Card.config []
          |> Card.header [ class "text-center" ]  
              [ h3 [ class "mt-2" ] [text title] ]
          |> Card.block []
            [ Card.custom <|
               Grid.container [class "pre-scrollable", style [("text-align","center")]]
                        ( List.map (\{full_name,score} ->
                            Grid.row []
                              [ Grid.col []
                                [ label [] [text full_name]]
                              , Grid.col []
                                [ label [] [text score]]
                              ]
                        ) model.recommendation)
            ]
          |> Card.view 
      ]
    else
      [text ""]
    


view : Model -> Html Msg
view model =
  div []
  [ Grid.container []
    [ CDN.stylesheet -- creates an inline style node with the Bootstrap CSS
    , Grid.row []      

        [ Grid.col [] 
          [ Form.formInline [] 
            [ Input.text [ Input.attrs [placeholder "User name"], Input.onInput ChgName]  
            , Button.button [Button.primary, Button.onClick CreateUser, Button.attrs [ class "ml-sm-2 my-2" ] ] [ text "New User" ] 
            , Button.button [ Button.info, Button.onClick SaveArtistsOfUser,Button.attrs [ class "ml-sm-2 my-2" ] ] [ text "Recommend" ] 
            , Button.button [ Button.danger, Button.onClick Cancel,Button.attrs [ class "ml-sm-2 my-2" ] ] [ text "Clear" ] 
            ]
          ]
        ]
    , Grid.row []
        [ Grid.col [Col.xs4 ]
          (viewAllArtists model)  

        , Grid.col [ Col.xs4]
          (viewSelected model)
        
        , Grid.col [ Col.xs4]
          (viewRecommendation model)
        ]
    ]
  ]