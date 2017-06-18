
import Debug exposing (log)
import Json.Decode exposing (field, int, string, list, Decoder)
import Json.Encode exposing (encode, object,string, int, Value)

import Html exposing (text, div, input, button, p, select,label,h1,h2,h3,h4,h5,h6,fieldset, Html)
import Html.Attributes exposing (value,multiple,style)
import Html.Events exposing (onClick, onInput)
import Html exposing (program)
import Http exposing (get, post, request, jsonBody, Error, Response, Error(..), Body)
import Task  exposing (Task, succeed, fail, andThen, mapError)   

import Bootstrap.CDN as CDN
import Bootstrap.Grid as Grid
import Bootstrap.Grid.Col as Col
import Bootstrap.Grid.Row as Row 
import Bootstrap.Button as Button

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
type alias NewUser =
  { user_id: String
  , artists: List (Artist)
  }
  
type alias Artist =
  { id : String
  , full_name : String
  }

type alias Model =
  { user_id: String
  , artists : List Artist
  , selected: List Artist
  , created: Bool
  }

model : Model
model =
  { user_id = ""
  , artists=[] 
  , selected=[]
  , created = False
  }

init : (Model, Cmd Msg)
init =
  ( model, Cmd.none )

newUserDecoder : Decoder NewUser
newUserDecoder =
    Json.Decode.map2 NewUser
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
  = GetAllArtists
  | AddArtist (Artist)
  | LoadArtists (Result Http.Error (NewUser))
  | Cancel
  | Save
  | SaveArtist (Result Http.Error String)

update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  case msg of
    AddArtist artist->
      if (List.member artist model.selected) then
        (model, Cmd.none)
      else
        ({model | selected=artist::model.selected} , Cmd.none)  
        
    GetAllArtists ->
      (model, getAllArtists "")

    LoadArtists (Ok new_user) ->
      ( { model | user_id= new_user.user_id, artists=new_user.artists, created = True }, Cmd.none)

    LoadArtists (Err _) ->
      ( model, Cmd.none)

    Cancel ->
      ({ model | selected = [], created = False }, Cmd.none)

    SaveArtist (Ok _) ->
      ({model | selected=[]}, Cmd.none)


    SaveArtist (Err _) ->
      (model, Cmd.none)

    Save ->
      (model, saveUser model)            
     -- Boilerplate: Mdl action handler.


encodeSelectedArtists: List Artist -> Value
encodeSelectedArtists selectionList =
  Json.Encode.list 
    ( List.map (\{id} -> (encodeSelectedArtist id)) selectionList)

encodeSelectedArtist: String -> Value
encodeSelectedArtist id = 
  object
    [ ("id", Json.Encode.string id)
    , ("times", Json.Encode.int 1) --TODO: edit times
    ]

saveUser : Model -> Cmd Msg
saveUser model = 
  let 
    json = Http.jsonBody <| 
      object
        [ ( "selected", (encodeSelectedArtists model.selected))
        , ( "user_id",  (Json.Encode.string model.user_id ))
        ]
  in 
    sendPost SaveArtist ("http://localhost:8887/user") Json.Decode.string json



getAllArtists : String -> Cmd Msg
getAllArtists _=
  sendGet LoadArtists ("http://localhost:8887/new_user") newUserDecoder

sendGet : (Result Error a -> msg) -> String -> Decoder a -> Cmd msg
sendGet msg url decoder =
  Http.get url decoder |> Http.send msg

sendPost : (Result Error String -> msg) -> String -> Decoder String -> Body -> Cmd msg
sendPost msg url decoder body2 =
    Http.post url body2 decoder |> Http.send msg
    


-- VIEW
viewAllArtists: Model -> List (Html Msg)
viewAllArtists model=
  let 
    title = if model.created then "Artists" else ""
  in
    [ div []
      [ h6 [] [text title]
      , Grid.container []
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
  ]

viewSelected: Model -> List (Html Msg) 
viewSelected model=
  let 
    title = if model.created then "Selected: "++model.user_id else ""
  in
    [ div []
      [ h6 [] [text title]
      , Grid.container []
                ( List.map (\artist ->
                    Grid.row []
                      [ Grid.col []
                        [ label [] [text artist.full_name]]
                      ]
                ) model.selected)
      ]
    ]

viewButtons: Model -> List (Grid.Column Msg)
viewButtons model = 
  let 
    st = if model.created then (style [("display","visible")]) 
        else (style [("display","visible")])
  in
    [ Grid.col [Col.xs6, Col.attrs [st]]
          [ Button.button 
            [ Button.small
            , Button.primary
            , Button.onClick Save
            ] 
            [ text "Save" ] 
          ]
    , Grid.col [Col.xs6, Col.attrs [st]]
          [ Button.button 
            [ Button.small
            , Button.danger
            , Button.onClick Cancel 
            ] 
            [ text "Cancel" ] ]
    ]

view : Model -> Html Msg
view model =
  Grid.container []
  [ CDN.stylesheet -- creates an inline style node with the Bootstrap CSS
  , Grid.row []
      [ Grid.col [Col.xs12]
        [ Button.button [Button.primary, Button.onClick GetAllArtists ] [ text "New User" ] ]
      ]
  , Grid.row []
      [ Grid.col [Col.xs6 ]
        (viewAllArtists model)  

      , Grid.col [ Col.xs6]
        (viewSelected model)
      ]
  , Grid.row []
      (viewButtons model)
  ]