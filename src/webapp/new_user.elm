
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
import Bootstrap.ButtonGroup as ButtonGroup


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

type alias Tag =
  { id : String
  , full_name : String
  }

--type RadioState = Tags | Artists
type RadioState
    = Tags
    | Users
    
type alias Model =
  { user_id: String
  , user_name: String
  , artists : List Artist
  , selected: List Artist
  , recommendation: List ArtistRecommendation
  , created: Bool
  , tags: List Tag
  , radioState: RadioState
  }

model : Model
model =
  { user_id=""
  , user_name =""
  , artists=[] 
  , selected=[]
  , recommendation=[]
  , created = False
  , tags = []
  , radioState = Users
  }

init : (Model, Cmd Msg)
init =
  ( model, getTags )

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

listTagsDecoder: Decoder (List Tag)
listTagsDecoder=
  Json.Decode.list tagsDecoder

tagsDecoder : Decoder Tag
tagsDecoder =
    Json.Decode.map2 Tag
        (field "id"   Json.Decode.string)
        (field "full_name"  Json.Decode.string)

-- update

type Msg
  = 
  ChgName String
  | AddArtist (Artist)
  | Cancel
  | GetTagsRequest
  | GetTagsResponse (Result Http.Error (List Tag))
  | RecommendationRequest
  | RecommendationResponse (Result Http.Error (List ArtistRecommendation))
  | GetArtistsResponse (Result Http.Error (List Artist))
  | GetArtistsRequest (Tag)
  | RadioMsg (RadioState)




update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    
    ChgName name ->
      ({model| user_name = name}, Cmd.none)

    AddArtist artist ->
      if (List.member artist model.selected) then
        (model, Cmd.none)
      else
        ({model | selected=artist::model.selected} , Cmd.none)  
        
    Cancel ->
      ({ model | artists=[],  recommendation=[],created = False }, Cmd.none)

    RecommendationResponse (Ok res) ->
      ({model | recommendation=res, created = False}, Cmd.none)

    RecommendationResponse (Err _) ->
      (model, Cmd.none)

    RecommendationRequest ->
      (model, recommendation model)            
      
    GetArtistsRequest (tag) ->
      (model, getArtists(tag.id))

    GetArtistsResponse (Ok res) ->
      ({model|artists = res}, Cmd.none)

    GetArtistsResponse (Err r_) ->
      (model, Cmd.none)    

    GetTagsRequest ->
      (model, getTags)

    GetTagsResponse (Ok res) ->
      ({model|tags = res}, Cmd.none)

    GetTagsResponse (Err r_) ->
      (model, Cmd.none)    

    RadioMsg (rs) ->
      ({model|radioState = rs},Cmd.none)

    

encodeSelectedArtists: List Artist -> Value
encodeSelectedArtists selectionList =
  object    
      ( List.map (\{id} -> ( id,Json.Encode.int 1)) selectionList)
    

recommendation : Model -> Cmd Msg
recommendation model = 
  let 
    kindOfSim = if model.radioState==Users then "users" else "tags"
    json = Http.jsonBody <| 
      object
        [ ( "selected", (encodeSelectedArtists model.selected)),
          ( "kindOfSim", (Json.Encode.string kindOfSim))
        ]
  in 
    sendPost RecommendationResponse ("http://localhost:8887/recommendation") recommendationDecorder json


getArtists: String -> Cmd Msg
getArtists tag_id =
  sendGet GetArtistsResponse ("http://localhost:8887/artists/"++ tag_id) listArtistsDecoder

getTags:  Cmd Msg
getTags =
  sendGet GetTagsResponse ("http://localhost:8887/tags") listTagsDecoder

sendGet : (Result Error a -> msg) -> String -> Decoder a -> Cmd msg
sendGet msg url decoder =
  Http.get url decoder |> Http.send msg

sendPost : (Result Error a -> msg) -> String -> Decoder a -> Body -> Cmd msg
sendPost msg url decoder body2 =
    Http.post url body2 decoder |> Http.send msg
    
-- VIEW

showSelection : Model -> Bool
showSelection model = True --model.created || model.recommendation /= []

viewAllTags: Model -> List (Html Msg)
viewAllTags model=
  let 
    title = if (showSelection model) then "Tags" else ""
  in
    if (showSelection model) then
      [ Card.config []
          |> Card.header [ class "text-center" ]  
              [ h3 [ class "mt-2" ] [text title] ]
          |> Card.block []
            [ Card.custom <|
                Grid.container [class "pre-scrollable",style [("text-align","left")]]
                  (List.map (\tag -> 
                      Grid.row []
                        [ Grid.col []
                            [ Button.button 
                              [ Button.roleLink
                              , Button.onClick (GetArtistsRequest tag)
                              , Button.attrs [ style [("font-size","0.8rem")]]
                              ] [text tag.full_name]
                            ]
                        ]
                  ) model.tags)
            ]
          |> Card.view 
      ]
    else
      [text ""]
    

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
                Grid.container [class "pre-scrollable"]
                  (List.map (\artist -> 
                      Grid.row []
                        [ Grid.col [] 
                            [ label [style [("font-size","0.8rem"), ("text-align","left")]] [ text artist.full_name ]]
                        , Grid.col []
                            [ Button.button 
                              [ Button.roleLink
                              , Button.onClick (AddArtist artist)
                              , Button.attrs [style [("font-size","0.8rem"), ("text-align","right")]]
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
                Grid.container [class "pre-scrollable", style [("text-align","center"),("font-size","0.8rem")]]
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
        [ Card.config []
          |> Card.header [ class "text-center" ]  
              [ h3 [ class "mt-2" ] [text title] ]
          |> Card.block []
            [ Card.custom <|
               Grid.container [class "pre-scrollable"]
                        ( List.map (\{full_name,score} ->
                            Grid.row []
                              [ Grid.col []
                                [ label [style [("font-size","0.8rem"),("text-align","left")]] [text full_name]]
                              , Grid.col []
                                [ label [style [("font-size","0.8rem"),("text-align","right")]] [text score]]
                              ]
                        ) model.recommendation)
            ]
          |> Card.view 
        ]
    else
      [ text ""]

view : Model -> Html Msg
view model =
  div []
  [ Grid.container []
    [ CDN.stylesheet -- creates an inline style node with the Bootstrap CSS
    , Grid.row []      
        [ Grid.col [Col.xs8] 
          []
        , Grid.col [Col.xs4, Col.attrs [ style [("float","right")]]]
          [ 
            Button.button [ Button.small, Button.success, Button.onClick RecommendationRequest,Button.attrs [ class "ml-sm-2 my-2" ] ] [ text "Recommend" ] 
          , ButtonGroup.radioButtonGroup []
              [ ButtonGroup.radioButton
                  (model.radioState == Users)
                  [ Button.small, Button.primary, Button.attrs [ class "ml-sm-2 my-2" ], Button.onClick (RadioMsg Users) ]
                  [ text "Users" ]
              , ButtonGroup.radioButton
                  (model.radioState == Tags)
                  [ Button.small, Button.primary, Button.attrs [ class "ml-sm-2 my-2" ], Button.onClick (RadioMsg Tags) ]
                  [ text "Tags" ]
              ]
          , Button.button [ Button.small, Button.danger, Button.onClick Cancel,Button.attrs [ class "ml-sm-2 my-2" ] ] [ text "Clear" ]               
          ]
        ]
    , Grid.row []
        [ Grid.col [Col.xs3 ]
          (viewAllTags model)  
        , Grid.col [Col.xs3 ]
          (viewAllArtists model)  

        , Grid.col [ Col.xs3]
          (viewSelected model)
        
        , Grid.col [ Col.xs3]
           (viewRecommendation model)
          
        ]
    ]
  ]